%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

%global gem_name mongo

# Fallback to rh-mongodb26. rh-mongodb26-scldevel is probably not available in
# the buildroot.
%{!?scl_mongodb:%global scl_mongodb rh-mongodb32}
%{!?scl_prefix_mongodb:%global scl_prefix_mongodb %{scl_mongodb}-}

%global enable_tests 1

Name:          %{?scl_prefix}rubygem-%{gem_name}
Version:       2.2.3
Release:       5%{?dist}
Summary:       Ruby driver for MongoDB
Group:         Development/Languages
License:       ASL 2.0
URL:           http://www.mongodb.org
Source0:       http://rubygems.org/gems/%{gem_name}-%{version}.gem

Requires:      %{?scl_prefix_ruby}ruby(release)
Requires:      %{?scl_prefix_ruby}ruby(rubygems)
Requires:      %{?scl_prefix}rubygem(bson) => 4.0
Requires:      %{?scl_prefix}rubygem(bson) < 5
BuildRequires: %{?scl_prefix_ruby}ruby(release)
BuildRequires: %{?scl_prefix_ruby}rubygems-devel
# For running the tests
BuildRequires: %{?scl_prefix}rubygem(bson)
BuildRequires: %{?scl_prefix}rubygem(rspec)
BuildArch:     noarch
Provides:      %{?scl_prefix}rubygem(%{gem_name}) = %{version}

# Explicitly require runtime subpackage, as long as older scl-utils do not generate it
Requires: %{?scl_prefix}runtime

BuildRequires: %{?scl_prefix_mongodb}mongodb-server

%description
A Ruby driver for MongoDB. For more information about Mongo, see
http://www.mongodb.org.

%package doc
Summary: Documentation for %{pkg_name}
Requires:%{?scl_prefix}%{pkg_name} = %{version}-%{release}

%description doc
Documentation for %{pkg_name}

%prep
%{?scl:scl enable %{scl} - << \EOF}
gem unpack %{SOURCE0}
%{?scl:EOF}
%setup -q -D -T -n  %{gem_name}-%{version}

%{?scl:scl enable %{scl} - << \EOF}
gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec
%{?scl:EOF}

%build
mkdir -p .%{gem_dir}

# Fix missing wrapper for mongo_console executable
# https://bugzilla.redhat.com/show_bug.cgi?id=1315283
# https://github.com/mongodb/mongo-ruby-driver/pull/756
sed -i "/require_paths/i   s.executables       = ['mongo_console']" mongo.gemspec

# Create the gem as gem install only works on a gem file
%{?scl:scl enable %{scl} - << \EOF}
gem build %{gem_name}.gemspec
%gem_install
%{?scl:EOF}

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}%{_bindir}
cp -a .%{_bindir}/* %{buildroot}%{_bindir}

%check
%if 0%{?enable_tests}
%{?scl:scl enable %{scl} %{scl_mongodb} - << \EOF}
set -e
pushd .%{gem_instdir}

# Create data directory and start testing mongo instance.
mkdir data
mongod \
  --dbpath data \
  --logpath data/log \
  --fork \
  --bind_ip 127.0.0.1 \
  --auth

CI="travis" rspec spec

# Shutdown mongo and cleanup the data.
mongod --shutdown --dbpath data
rm -rf data
popd
%{?scl:EOF}
%endif

%files
%{gem_instdir}/LICENSE
%dir %{gem_instdir}
%{_bindir}/mongo_console
%{gem_instdir}/bin/
%{gem_libdir}
%{gem_spec}
%exclude %{gem_cache}

%files doc
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/CONTRIBUTING.md
%doc %{gem_docdir}
%doc %{gem_instdir}/Rakefile
%{gem_instdir}/mongo.gemspec
%{gem_instdir}/spec

%changelog
* Mon Apr 18 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-5
- Use rspec tests

* Tue Apr 12 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-4
- Fix Fix missing wrapper for mongo_console executable
  - Resolves: rhbz#1315283

* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-3
- Add rubygem-shoulda to BuildReqires (for tests)

* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-2
- Enable tests

* Mon Feb 29 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-1
- Update to 2.2.3

* Tue Feb 16 2016 Troy Dawson <tdawson@redhat.com> - 1.10.2-5
- Disable tests until mongodb becomes stable in rawhide again.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jul 27 2015 Troy Dawson <tdawson@redhat.com> - 1.10.2-2
- Fix tests

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 26 2014 Vít Ondruch <vondruch@redhat.com> - 1.10.2-1
- Update to mongo 1.10.2.

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Nov 19 2013 Vít Ondruch <vondruch@redhat.com> - 1.9.2-1
- Update to mongo 1.9.2.
- Enabled test suite.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Mar 13 2013 Troy Dawson <tdawson@redhat.com> - 1.6.4-4
- Fix to make it build/install on F19+

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Aug 10 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-2
- Fixed doc
- removed more BuildRequires that are not required

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-1
- Updated to latest version
- Removed BuildRequires that are not needed

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-7
- Fixed checks.  
  Only run checks that do not require a running mongodb server

* Tue Aug 07 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-6
- Changed .gemspec and Rakefile to not be doc
- Added checks

* Thu Aug 02 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-5
- Fixed rubygem(bson) requires

* Mon Jul 23 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-4
- Updated to meet new fedora rubygem guidelines

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-3
- Changed group to Development/Languages
- Changed the global variables
- Seperated the doc and test into the doc rpm

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-2
- Added %{?dist} to version

* Tue Nov 15 2011  <tdawson@redhat.com> - 1.4.0-1
- Initial package
